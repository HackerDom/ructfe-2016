import Kitura
import SwiftyJSON


// let set = SortedSet<User>()

// var user1 = User("kost", "qwer") //7
// user1.comments.append(Comment(nil, nil, nil, 5))
// user1.comments.append(Comment(nil, nil, nil, 2))
// set.insert(user1)

// var user2 = User("dscheg", "qwer") //5
// user2.comments.append(Comment(nil, nil, nil, 1))
// user2.comments.append(Comment(nil, nil, nil, 4))
// set.insert(user2)

// var user3 = User("bay", "qwer") //6
// user3.comments.append(Comment(nil, nil, nil, 5))
// user3.comments.append(Comment(nil, nil, nil, 1))
// set.insert(user3)

// var user4 = User("kost", "qwer") //3
// user4.comments.append(Comment(nil, nil, nil, 5))
// user4.comments.append(Comment(nil, nil, nil, 2))
// set.insert(user4)

// var user5 = User("kost", "qwer") //3
// user5.comments.append(Comment(nil, nil, nil, 1))
// user5.comments.append(Comment(nil, nil, nil, 2))
// set.insert(user5)

// for item in set {
//     print(item.name + " " + String(item.rating()))
// }

// let user = User("kost", "pass")

// let jsonString = JSONSerializer.toJson(user)
// print(jsonString)

// var json = JSON.parse(string: jsonString)
// print(json["name"].string!)

let sapmarine = Sapmarine()
sapmarine.Run(port: 31337);