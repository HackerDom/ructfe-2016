import Foundation

public class Trip {
    let id: String = UUID().uuidString;

    let passenger: String;
    var driver: String;

    init(_ passenger: String, _ driver: String){
        // id = UUID().uuidString
        self.passenger = passenger
        self.driver = driver
    }
}