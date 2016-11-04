import Kitura

let router = Router()

router.get("/") {
    request, response, next in
    response.send("Hello, World!")
    next()
}

Kitura.addHTTPServer(onPort: 31337, with: router)
Kitura.run()

/*
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
*/