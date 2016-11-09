import SwiftyJSON

public class Comment{
    var driver:String? = nil
    var passenger:String? = nil
    var text:String? = nil
    var mark:Int = 0;

    // init(){
    // }

    init(_ driver: String?, _ passenger: String?, _ text: String?, _ mark: Int) {
        self.driver = driver
        self.passenger = passenger
        self.text = text
        self.mark = mark
    }

    init(json: JSON) {
        driver = json["driver"].stringValue
        passenger = json["passenger"].stringValue
        text = json["text"].stringValue
        mark = json["text"].int!
    }

    public func toJson() -> String {
        return JSONSerializer.toJson(self)
    }
}