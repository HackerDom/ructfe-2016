public class User : Comparable {
    var login: String
    var passHash: String
    var comments = [Comment]()

    init(_ login: String, _ passHash: String) {
        self.login = login
        self.passHash = passHash
    }

    public func rating() -> Int {
        return comments
            .filter { $0.mark != 0}
            .map { $0.mark }
            .reduce(0,+)
    }

    public static func < (lhs: User, rhs: User) -> Bool {
        if(lhs == rhs){
            return false;
        }

        let lhsRating = lhs.rating()
        let rhsRating = rhs.rating()
        if lhsRating != rhsRating {
            return lhsRating < rhsRating
        } else {
            return lhs.login < rhs.login
        }
    }

    public static func == (lhs: User, rhs: User) -> Bool {
        return lhs.login == rhs.login
    }
}