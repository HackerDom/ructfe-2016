public class Comment{
    var driver:String? = nil
    var passanger:String? = nil
    var text:String? = nil
    var mark:Int = 0;

    init(){
    }

    init(_ driver: String?, _ passanger: String?, _ text: String?, _ mark: Int) {
        self.driver = driver
        self.passanger = passanger
        self.text = text
        self.mark = mark
    }
}