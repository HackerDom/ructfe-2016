import Foundation
import Dispatch

import KituraSession
import KituraStencil
import SwiftyJSON
import Kitura
import Cryptor

#if os(Linux)
    import Glibc
#endif

public class Sapmarine {

    let dispatchQueue = DispatchQueue(label: "collectionsLockQueue")

    var usersSet: SortedSet<User> = SortedSet<User>()
    var usersDict: Dictionary<String, User> = Dictionary<String, User>()
    var profilesDict: Dictionary<String, Profile> = Dictionary<String, Profile>()
    let router: Router = Router()

    var newTrips: Dictionary<String, String> = Dictionary<String, String>()
    var processingTrips: Dictionary<String, Trip> = Dictionary<String, Trip>()

    init(){
        let saveStateTimer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { t in
            sapmarine.SaveState()
        }
        // RunLoop.current.add(saveStateTimer, RunLoop.currentMode)

        let session = Session(secret: UUID().uuidString)
        router.all(middleware: session)

        router.all(middleware: BodyParser())

        router.all("/static", middleware: StaticFileServer(path: "./static"))

        router.add(templateEngine: StencilTemplateEngine())

        router.get("/") { request, response, next in
            defer {
                next()
            }

            let userNameOptional = try self.GetUserFromSession(request, response)

            var stencilContext: [String: Any] = [:]
            self.dispatchQueue.sync {
                let allTripsArray = self.newTrips.map { (key, value) in ["passenger": key, "description": value] }
                let driversTripsArray = self.processingTrips
                    .filter { (key, value) in userNameOptional != nil && value.driver == userNameOptional!}
                    .map { (key, value) in ["passenger": value.passenger, "driver": value.driver, "id": value.id, "isMine": "1"] }

                stencilContext = [
                    "isLoggedIn": userNameOptional != nil,
                    "user": userNameOptional ?? "",
                    "users": self.usersSet.map { ["name": $0.name, "rating": $0.rating()] },
                    "trips": driversTripsArray + allTripsArray
                ]
            }

            try response.render("index.stencil", context: stencilContext).end()
        }

        router.get("/loginForm") { request, response, next in
            let stencilContext: [String: Any] = [:]
            try response.render("login.stencil", context: stencilContext).end()
        }

        router.get("/login") { request, response, next in
            let user = self.FindParam(request, "user")
            let pass = self.FindParam(request, "pass")

            if user == "" || pass == "" {
                response.statusCode = .badRequest
                try response.send("Params 'user' and 'pass' can't be empty").end()
                return;
            }

            if self.FindExistingUserOrRegister(user, pass) == nil {
                response.statusCode = .forbidden
                try response.send("User '\(user)' can't be logged in or registered").end()
                return
            }

            let sess = request.session!
            sess["user"] = JSON(user)

            try response.redirect("/").end()
        }

        router.get("/logout") { request, response, next in
            let sess = request.session!
            sess.destroy() { (error: Error?) in }
            try response.redirect("/").end()
        }

        router.get("/setProfile") { request, response, next in
            let userNameOptional = try self.GetUserFromSessionOrCancelRequest(request, response)
            if userNameOptional == nil { return }

            let fullName = self.FindParam(request, "fullName")
            let job = self.FindParam(request, "job")
            let notes = self.FindParam(request, "notes")

            if fullName == "" || job == "" || notes == ""{
                response.statusCode = .badRequest
                try response.send("Params 'fullName', 'job', 'notes' can't be empty").end()
                return;
            }

// self.dispatchQueue.sync {
                if self.profilesDict[userNameOptional!] != nil{
                    response.statusCode = .forbidden
                    try response.send("Profile is already set and can't be changed").end()
                    return
                }

                self.profilesDict[userNameOptional!] = Profile(fullName, job, notes)
// }

            try response.redirect("/profileForm").end()
        }

        router.get("/profileForm") { request, response, next in
            let userNameOptional = try self.GetUserFromSessionOrCancelRequest(request, response)
            if userNameOptional == nil { return }

            var stencilContext: [String: Any] = [:]
            self.dispatchQueue.sync {

                let profile = self.profilesDict[userNameOptional!]

                stencilContext = [
                    "isLoggedIn": userNameOptional != nil,
                    "isProfileFilledIn": self.profilesDict[userNameOptional!] != nil,
                    "user": userNameOptional!,
                    "fullName": profile?.fullName,
                    "job": profile?.job,
                    "notes": profile?.notes,
                ]
            }

            try response.render("profile.stencil", context: stencilContext).end()
        }

        router.get("/addTrip") { request, response, next in
            let userNameOptional = try self.GetUserFromSessionOrCancelRequest(request, response)
            if userNameOptional == nil { return }

            let description = self.FindParam(request, "description");

            if description == "" {
                response.statusCode = .badRequest
                try response.send("Param 'description' can't be empty").end();
                return;
            }

            self.dispatchQueue.sync {
                self.newTrips[userNameOptional!] = description
            }

            try response.end()
        }

        router.get("/takeTrip") { request, response, next in
            let driverNameOptional = try self.GetUserFromSessionOrCancelRequest(request, response)
            if driverNameOptional == nil { return }

            let passengerName = self.FindParam(request, "passenger");
            if passengerName == "" {
                response.statusCode = .badRequest
                try response.send("Param 'passenger' can't be empty").end();
                return;
            }

            let trip = Trip(passengerName, driverNameOptional!)
            self.dispatchQueue.sync {
                self.newTrips.removeValue(forKey: passengerName)
                self.processingTrips[trip.id] = trip
            }

            try response.send(trip.id).end()
        }

        router.get("/reviewForm") { request, response, next in
            let userNameOptional = try self.GetUserFromSessionOrCancelRequest(request, response)
            if userNameOptional == nil { return }

            let tripId = self.FindParam(request, "tripId")
            if tripId == "" {
                response.statusCode = .badRequest
                try response.send("Param tripId should contain trip id").end();
                return
            }

            var stencilContext: [String: Any] = [:]

            stencilContext = [
                "isLoggedIn": userNameOptional != nil,
                "user": userNameOptional!,
                "tripId": tripId
            ]

            try response.render("review.stencil", context: stencilContext).end()
        }

        router.get("/finishTrip") { request, response, next in
            let driverNameOptional = try self.GetUserFromSessionOrCancelRequest(request, response)
            if driverNameOptional == nil { return }

            let tripId = self.FindParam(request, "tripId")
            let comment = self.FindParam(request, "comment")
            let markOptional = Int(self.FindParam(request, "mark"))

            if tripId == "" || comment == "" || markOptional == nil || markOptional! > 5 || markOptional! < 1{
                response.statusCode = .badRequest
                try response.send("Param tripId should contain trip id, param 'comment' can't be empty and param 'mark' should be an integer in [1..5]").end();
                return
            }

            if let trip = self.processingTrips.removeValue(forKey: tripId) {

                self.dispatchQueue.sync {
                    let passengerName = trip.passenger

                    let passengerOptional = self.usersDict[passengerName]
                    if(passengerOptional == nil){
                        response.statusCode = .badRequest
                        return
                    }

                    // TODO create method addAfterRemove
                    self.usersSet.remove(passengerOptional!)
                    passengerOptional!.comments.append(Comment(driverNameOptional!, passengerName, comment, markOptional!))
                    self.usersSet.insert(passengerOptional!)
                }

                try response.end()
            } else {
                response.statusCode = .notFound
                try response.send("Trip with tripId '\(tripId)' not found in processing trips").end();
            }
        }
    }

    public func SaveState() {
        self.dispatchQueue.sync {
            
        }
    }

    public func SaveUsers() {

    }

    public func SaveProfiles() {

    }

    public func SaveTrips() {

    }

    public func Start(port: Int) {
        Kitura.addHTTPServer(onPort: port, with: router)
        Kitura.start()
    }

    private func FindExistingUserOrRegister(_ user: String, _ pass: String) -> User? {
        let digest = Digest(using: .sha1).update(string: pass)!.final();
        let passHash = CryptoUtils.hexString(from: digest);
        let user = User(user, passHash)

        var result : User?
        self.dispatchQueue.sync {
            if let existingUser = usersSet.find(user) {
                result = existingUser.passHash == user.passHash ? existingUser : nil;
            } else {
                usersSet.insert(user)
                usersDict[user.name] = user
                result = user
            }
        }
        return result
    }

    private func FindParam(_ request: RouterRequest, _ paramName: String) -> String {
        return request.queryParameters[paramName]?.trim() ?? "";
    }

    private func GetUserFromSessionOrCancelRequest(_ request: RouterRequest, _ response: RouterResponse) throws -> String? {
        let user = try GetUserFromSession(request, response)
        if(user == nil) {
            response.statusCode = .forbidden
            try response.send("User not logged in").end()
        }
        return user
    }

    private func GetUserFromSession(_ request: RouterRequest, _ response: RouterResponse) throws -> String? {
        let sess = request.session!
        let user = sess["user"].string
        return user
    }
}