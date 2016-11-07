import Foundation

public class Profile {
    var fullName: String
    var job: String
    var notes: String

    init(_ fullName: String, _ job: String, _ notes: String) {
        self.fullName = fullName
        self.job = job
        self.notes = notes
    }
}