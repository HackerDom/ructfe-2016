import SwiftyJSON

public class Comment{
    var driver:String? = nil
    var passenger:String? = nil
    var text:String? = nil
    var mark:Int = 0;

    init(_ driver: String?, _ passenger: String?, _ text: String?, _ mark: Int) {
        self.driver = driver
        self.passenger = passenger
        self.text = text
        self.mark = mark
    }

    convenience init(_ jsonString : String) {
        let dataFromString = jsonString.data(using: .utf8, allowLossyConversion: false)!
        let json = JSON(data: dataFromString)
        self.init(json)
    }

    init(_ json: JSON) {
        driver = json["driver"].stringValue
        passenger = json["passenger"].stringValue
        text = json["text"].stringValue
        if json["mark"].int != nil {
            mark = json["mark"].int!
        }
    }

    public func toJson() -> String {
        return JSONSerializer.toJson(self)
    }
}