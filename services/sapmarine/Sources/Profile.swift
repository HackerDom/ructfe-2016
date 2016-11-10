import SwiftyJSON
import Foundation

public class Profile {
    var name: String
    var fullName: String
    var job: String
    var notes: String

    init(_ name: String, _ fullName: String, _ job: String, _ notes: String) {
        self.name = name
        self.fullName = fullName
        self.job = job
        self.notes = notes
    }

    convenience init(_ jsonString : String) {
        let dataFromString = jsonString.data(using: .utf8, allowLossyConversion: false)!
        let json = JSON(data: dataFromString)
        self.init(json)
    }

    init(_ json: JSON) {
        name = json["name"].stringValue
        fullName = json["fullName"].stringValue
        job = json["job"].stringValue
        notes = json["notes"].stringValue
    }

    public func toJson() -> String {
        return JSONSerializer.toJson(self)
    }
}