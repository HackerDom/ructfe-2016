public class Comment{
    var driver:String? = nil
    var passenger:String? = nil
    var text:String? = nil
    var mark:Int = 0;

    init(){
    }

    init(_ driver: String?, _ passenger: String?, _ text: String?, _ mark: Int) {
        self.driver = driver
        self.passenger = passenger
        self.text = text
        self.mark = mark
    }
}