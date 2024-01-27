import SwiftUI

@main
struct nlp_terminal_frontendApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        MenuBarExtra("Menu", systemImage: "sparkles") {
            Menu()
        }
        .menuBarExtraStyle(.window)
    }
}
