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