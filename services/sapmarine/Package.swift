import PackageDescription

let package = Package(
    name: "sapmarine",
    dependencies: [
        .Package(url: "https://github.com/IBM-Swift/Kitura.git", majorVersion: 1, minor: 1),
        .Package(url: "https://github.com/IBM-Swift/BlueCryptor", majorVersion: 0, minor: 7),
//        .Package(url: "Packages/Algorithm-1.0.8", majorVersion: 1)
    ])
