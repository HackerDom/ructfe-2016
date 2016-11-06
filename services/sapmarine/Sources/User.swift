public class User : Comparable {
    var name: String
    var passHash: String
    var comments = [Comment]()

    init(_ name: String, _ passHash: String) {
        self.name = name
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
            return lhs.name < rhs.name
        }
    }

    public static func == (lhs: User, rhs: User) -> Bool {
        return lhs.name == rhs.name
    }
}