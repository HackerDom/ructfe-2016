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

    init(json: JSON) {
        name = json["name"].stringValue
        fullName = json["fullName"].stringValue
        job = json["job"].stringValue
        notes = json["notes"].stringValue
    }

    public func toJson() -> String {
        return JSONSerializer.toJson(self)
    }
}