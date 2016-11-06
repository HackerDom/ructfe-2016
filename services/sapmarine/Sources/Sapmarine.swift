import Foundation

import KituraSession
import SwiftyJSON
import Kitura
import Cryptor

public class Sapmarine {

    let users: SortedSet<User> = SortedSet<User>()
    let router: Router = Router()

    var newTrips: Dictionary<String, String> = Dictionary<String, String>()
    var processingTrips: Dictionary<String, Trip> = Dictionary<String, Trip>()

    init(){
        let session = Session(secret: "hackerdom")
        router.all(middleware: session)

        router.all(middleware: BodyParser())

        router.get("/login") { request, response, next in
            let user = self.FindParam(request, "user");
            let pass = self.FindParam(request, "pass");

            if user == "" || pass == "" || !self.FindExistingUserOrRegister(user, pass) {
                response.statusCode = .forbidden
                try response.send("User '\(user)' can't be logged in or registered").end();
                return;
            }

            let sess = request.session!
            sess["user"] = JSON(user)

            try response.redirect("/").end()
            // try response.send("Sucessfully registered new user '\(user)'").end();
        }

        router.get("/addTrip") { request, response, next in
            let user = try self.GetUserFromSessionOrCancelRequest(request, response)
            if user == "" {
                return
            }

            let description = self.FindParam(request, "description");

            if description == "" {
                response.statusCode = .badRequest
                try response.send("Param 'description' can't be empty").end();
                return;
            }

            self.newTrips[user] = description;
            try response.end();
        }

        router.get("/takeTrip") { request, response, next in
            let driver = try self.GetUserFromSessionOrCancelRequest(request, response)
            if(driver == "") {
                return
            }

            let passenger = self.FindParam(request, "passenger");
            if passenger == "" {
                response.statusCode = .badRequest
                try response.send("Param 'passenger' can't be empty").end();
                return;
            }

            self.newTrips.removeValue(forKey: passenger)

            let trip = Trip(passenger, driver)
            self.processingTrips[trip.id] = trip

            try response.send(trip.id).end();
        }

        router.get("/finishTrip") { request, response, next in
            let driver = try self.GetUserFromSessionOrCancelRequest(request, response)
            if(driver == "") {
                return
            }

            let tripId = self.FindParam(request, "tripId");
            let comment = self.FindParam(request, "comment");
            let mark = Int(self.FindParam(request, "mark"));

            if comment == "" || mark == nil || mark! > 5 || mark! < 1{
                response.statusCode = .badRequest
                try response.send("Param 'comment' can't be empty and param 'mark' should be an integer in [1..5]").end();
                return;
            }

            if let trip = self.processingTrips.removeValue(forKey: tripId) {
                try response.send(trip.id).end();
            } else {
                response.statusCode = .notFound
                try response.send("Trip with id '\(tripId)' not found in processing trips").end();
                return;
            }
        }

        router.get("/") { request, response, next in
            let sess = request.session

            if let sess = sess, let user = sess["user"].string {
                try response.send("User '\(user)'").end()
            } else {
               try response.send("No user logged in").end()
            }
        }

    }

    public func Run(port: Int){
        Kitura.addHTTPServer(onPort: port, with: router)
        Kitura.run()
    }

    private func FindExistingUserOrRegister(_ user: String, _ pass: String) -> Bool{
        let digest = Digest(using: .sha1).update(string: pass)!.final();
        let passHash = CryptoUtils.hexString(from: digest);
        let user = User(user, passHash)

        //TODO lock on find and insert
        if let existingUser = users.find(user) {
            return existingUser.passHash == user.passHash;
        }

        users.insert(user);
        return true;
    }

    private func FindParam(_ request: RouterRequest, _ paramName: String) -> String {
        return request.queryParameters[paramName]?.trim() ?? "";
    }

    public func GetUserFromSessionOrCancelRequest(_ request: RouterRequest, _ response: RouterResponse) throws -> String {
        let sess = request.session!
        let user = sess["user"].string ?? ""

        if(user == "") {
            response.statusCode = .forbidden
            try response.send("User not logged in").end()
        }

        return user;
    }
}