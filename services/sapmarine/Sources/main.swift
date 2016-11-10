import Foundation
import Kitura
import SwiftyJSON

let sapmarine = Sapmarine()
sapmarine.Start(port: 31337);

RunLoop.current.run()
