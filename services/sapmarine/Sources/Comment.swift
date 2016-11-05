public class Comment{
    var author:String? = nil
    var target:String? = nil
    var text:String? = nil
    var mark:Int = 0;

    init(){
    }

    init(_ author: String?, _ target: String?, _ text: String?, _ mark: Int) {
        self.author = author
        self.target = target
        self.text = text
        self.mark = mark
    }
}