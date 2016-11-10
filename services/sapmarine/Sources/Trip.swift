import SwiftyJSON
import Foundation

public class Trip {
    var id: String;
    var passenger: String;
    var driver: String;

    init(_ passenger: String, _ driver: String){
        id = UUID().uuidString;
        self.passenger = passenger
        self.driver = driver
    }

    convenience init(_ jsonString : String) {
        let dataFromString = jsonString.data(using: .utf8, allowLossyConversion: false)!
        let json = JSON(data: dataFromString)
        self.init(json)
    }

    init(_ json: JSON) {
        id = json["id"].stringValue
        passenger = json["passenger"].stringValue
        driver = json["driver"].stringValue
    }

    public func toJson() -> String {
        return JSONSerializer.toJson(self)
    }
}