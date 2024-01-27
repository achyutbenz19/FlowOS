import SwiftUI

struct ContentView: View {
    var body: some View {
        ZStack {
            VStack {
                HStack {
                    Image(systemName: "sparkles")
                    Text("Simplifying Commands with Natural Language")
                        .font(.headline)
                        .fontWeight(.bold)
                        .multilineTextAlignment(.center)
                }.padding(.top, 40).padding(.horizontal, 20)
                Spacer()
            }
            .frame(height: 100.0)
        }
    }
}

#Preview {
    ContentView()
}
