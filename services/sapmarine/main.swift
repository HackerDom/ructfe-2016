import Foundation

public class Comment{
    var author:String? = nil
    var user:String? = nil
    var text:String? = nil
    var mark:Int = 0;

    init(){
    }

    init(_ author: String?, _ user: String?, _ text: String?, _ mark: Int) {
        self.author = author
        self.user = user
        self.text = text
        self.mark = mark
    }
}

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

var user1 = User("kost")
user1.comments.append(Comment(nil, nil, nil, 5))
user1.comments.append(Comment(nil, nil, nil, 2))
var user2 = User("dscheg")
user2.comments.append(Comment(nil, nil, nil, 1))
user2.comments.append(Comment(nil, nil, nil, 4))
var user3 = User("bay")
user3.comments.append(Comment(nil, nil, nil, 5))
user3.comments.append(Comment(nil, nil, nil, 1))

var set = SortedSet(elements: user1, user2, user3)

for item in set {
    print(item.rating())
}