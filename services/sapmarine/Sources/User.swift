public class User : Comparable {
    var login: String?
    var comments = [Comment]()

    init(_ login: String) {
        self.login = login
    }

    public func rating() -> Int {
        return comments
            .filter { $0.mark != 0}
            .map { $0.mark }
            .reduce(0,+)
    }

    public static func < (lhs: User, rhs: User) -> Bool {
        return lhs.rating() < rhs.rating()
    }

    public static func == (lhs: User, rhs: User) -> Bool {
        return lhs.rating() == rhs.rating()
    }
}