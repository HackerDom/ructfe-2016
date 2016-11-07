import Foundation

import KituraSession
import KituraStencil
import SwiftyJSON
import Kitura
import Cryptor

#if os(Linux)
    import Glibc
#endif

public class Sapmarine {

    var usersSet: SortedSet<User> = SortedSet<User>()
    var usersDict: Dictionary<String, User> = Dictionary<String, User>()
    var profilesDict: Dictionary<String, Profile> = Dictionary<String, Profile>()
    let router: Router = Router()

    var newTrips: Dictionary<String, String> = Dictionary<String, String>()
    var processingTrips: Dictionary<String, Trip> = Dictionary<String, Trip>()

    init(){
        let session = Session(secret: UUID().uuidString)
        router.all(middleware: session)

        router.all(middleware: BodyParser())

        router.all("/static", middleware: StaticFileServer(path: "./static"))

        router.add(templateEngine: StencilTemplateEngine())

        router.get("/") { request, response, next in
            defer {
                next()
            }

            let userNameOptional = try self.GetUserFromSessionOrCancelRequest(request, response)
            if userNameOptional == nil {
                response.statusCode = .badRequest
                try response.end()
                return
            }

            let allTripsArray = self.newTrips.map { (key, value) in ["passenger": key, "description": value] }
            let driversTripsArray = self.processingTrips
                .filter { (key, value) in value.driver == userNameOptional!}
                .map { (key, value) in ["passenger": value.passenger, "driver": value.driver, "id": value.id] }

            let context: [String: Any] = [
                "users": self.usersSet.map { ["name": $0.name, "rating": $0.rating()] },
                "trips": driversTripsArray + allTripsArray
            ]

            try response.render("index.stencil", context: context).end()
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
            // sess["user"] = JSON.parse(string: JSONSerializer.toJson(userObj))
            sess["user"] = JSON(user)

            try response.redirect("/").end()
            // try response.send("Sucessfully registered new user '\(user)'").end();
        }

        router.get("/setProfile") { request, response, next in
            let userNameOptional = try self.GetUserFromSessionOrCancelRequest(request, response)
            if userNameOptional == nil {
                response.statusCode = .badRequest
                try response.end()
                return
            }

            let fullName = self.FindParam(request, "fullName")
            let job = self.FindParam(request, "job")
            let notes = self.FindParam(request, "notes")

            if fullName == "" || job == "" || notes == ""{
                response.statusCode = .badRequest
                try response.send("Params 'fullName', 'job', 'notes' can't be empty").end()
                return;
            }

            if self.profilesDict[userNameOptional!] != nil{
                response.statusCode = .forbidden
                try response.send("Profile is already set and can't be changed").end()
                return
            }

            self.profilesDict[userNameOptional!] = Profile(fullName, job, notes)

            try response.end()
        }

        router.get("/addTrip") { request, response, next in
            let userNameOptional = try self.GetUserFromSessionOrCancelRequest(request, response)
            if userNameOptional == nil {
                response.statusCode = .badRequest
                try response.end()
                return
            }

            let description = self.FindParam(request, "description");

            if description == "" {
                response.statusCode = .badRequest
                try response.send("Param 'description' can't be empty").end();
                return;
            }

            self.newTrips[userNameOptional!] = description
            try response.end()
        }

        router.get("/takeTrip") { request, response, next in
            let driverNameOptional = try self.GetUserFromSessionOrCancelRequest(request, response)
            if driverNameOptional == nil {
                response.statusCode = .badRequest
                try response.end()
                return
            }

            let passengerName = self.FindParam(request, "passenger");
            if passengerName == "" {
                response.statusCode = .badRequest
                try response.send("Param 'passenger' can't be empty").end();
                return;
            }

            self.newTrips.removeValue(forKey: passengerName)

            let trip = Trip(passengerName, driverNameOptional!)
            self.processingTrips[trip.id] = trip

            try response.send(trip.id).end()
        }

        router.get("/finishTrip") { request, response, next in
            let driverNameOptional = try self.GetUserFromSessionOrCancelRequest(request, response)
            if driverNameOptional == nil {
                response.statusCode = .badRequest
                try response.end()
                return
            }

            let tripId = self.FindParam(request, "tripId")
            let comment = self.FindParam(request, "comment")
            let markOptional = Int(self.FindParam(request, "mark"))

            if comment == "" || markOptional == nil || markOptional! > 5 || markOptional! < 1{
                response.statusCode = .badRequest
                try response.send("Param 'comment' can't be empty and param 'mark' should be an integer in [1..5]").end();
                return
            }

            if let trip = self.processingTrips.removeValue(forKey: tripId) {
                let passengerName = trip.passenger

                // print("Finishing trip '\(tripId)' for passenger '\(passengerName)'")

                let passengerOptional = self.usersDict[passengerName]
                if(passengerOptional == nil){
                    response.statusCode = .badRequest
                    try response.end()
                    return
                }

                // TODO create method addAfterRemove
                self.usersSet.remove(passengerOptional!)
                passengerOptional!.comments.append(Comment(driverNameOptional!, passengerName, comment, markOptional!))
                self.usersSet.insert(passengerOptional!)

                try response.end()
            } else {
                response.statusCode = .notFound
                try response.send("Trip with id '\(tripId)' not found in processing trips").end();
            }
        }

        router.get("/listUsers") { request, response, next in
            var result = "Users:\n"
            for user in self.usersSet {
                result += "\(user.name)\t\(user.rating())\n"
            }
            try response.send(result).end()
        }
    }

    public func Run(port: Int){
        Kitura.addHTTPServer(onPort: port, with: router)
        Kitura.run()
    }

    private func FindExistingUserOrRegister(_ user: String, _ pass: String) -> User?{
        let digest = Digest(using: .sha1).update(string: pass)!.final();
        let passHash = CryptoUtils.hexString(from: digest);
        let user = User(user, passHash)

        //TODO lock on find and insert
        if let existingUser = usersSet.find(user) {
            return existingUser.passHash == user.passHash ? existingUser : nil;
        }

        usersSet.insert(user)
        usersDict[user.name] = user
        return user
    }

    private func FindParam(_ request: RouterRequest, _ paramName: String) -> String {
        return request.queryParameters[paramName]?.trim() ?? "";
    }

    public func GetUserFromSessionOrCancelRequest(_ request: RouterRequest, _ response: RouterResponse) throws -> String? {
        let sess = request.session!
        let user = sess["user"].string
        if(user == nil) {
            response.statusCode = .forbidden
            try response.send("User not logged in").end()
        }

        return user
    }
}