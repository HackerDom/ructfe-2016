import Foundation

import KituraSession
import SwiftyJSON
import Kitura
import Cryptor

public class Sapmarine {

    let users: SortedSet<User>
    let router: Router

    init(){
        users = SortedSet<User>();

        router = Router()

        let session = Session(secret: "hackerdom")
        router.all(middleware: session)

        router.all(middleware: BodyParser())

        router.get("/login") { request, response, next in
            let user = (request.queryParameters["user"] ?? "").trim();
            let pass = (request.queryParameters["pass"] ?? "").trim();
            if(user == "" || pass == "" || !self.FindExistingUserOrRegister(user, pass)) {
                response.statusCode = .forbidden
                try response.send("User '\(user)' can't be logged in or registered").end();
                return;
            }

            let sess = request.session
            if let sess = sess { //TODO in which case it can be nil?
                sess["user"] = JSON(user)
            }

            try response.redirect("/").end()
            // try response.send("Sucessfully registered new user '\(user)'").end();
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
}