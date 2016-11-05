import Kitura
import Cryptor

public class Sapmarine {

    let users: SortedSet<User>
    let router: Router

    init(){
        users = SortedSet<User>();

        router = Router()
        router.get("/") { request, response, next in
            response.send("Hello, World!")
            next()
        }

        router.post("/register") { request, response, next in
            let login = (request.queryParameters["login"] ?? "").trim();
            let pass = (request.queryParameters["pass"] ?? "").trim();

            if(login == "" || pass == "" || !self.TryRegisterNewUser(login, pass)) {
                response.statusCode = .forbidden
                try response.send("User '\(login)' already exists").end();
                return;
            }

            try response.send("Sucessfully registered new user '\(login)'").end();
        }
    }

    public func Run(port: Int){
        Kitura.addHTTPServer(onPort: port, with: router)
        Kitura.run()
    }

    private func TryRegisterNewUser(_ login: String, _ pass: String) -> Bool{
        let digest = Digest(using: .sha1).update(string: pass)!.final();
        let passHash = CryptoUtils.hexString(from: digest);
        let user = User(login, passHash)

        if(users.contains(user)){
            return false;
        }

        users.insert(user);
        return true;
    }
}