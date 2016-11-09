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

    init(json: JSON) {
        id = json["id"].stringValue
        passenger = json["passenger"].stringValue
        driver = json["driver"].stringValue
    }

    public func toJson() -> String {
        return JSONSerializer.toJson(self)
    }
}