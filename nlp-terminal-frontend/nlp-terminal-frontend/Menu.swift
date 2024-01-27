import Foundation
import SwiftUI
import Speech

struct Menu: View {
    @State private var userInput: String = ""
    
    var body: some View {
        Form {
            Section {
                TextField("", text: $userInput, prompt: Text("Enter query"))
                    .textFieldStyle(RoundedBorderTextFieldStyle())
            }.padding(.bottom, 3)
            Section {
                HStack {
                    
                    Button(action: {
                        submitAction()
                    }) {
                        Image(systemName: "paperplane.fill")
                    }
                    
                    Button(action: {
                        activateMicrophone()
                    }) {
                        Image(systemName: "mic.fill")
                    }
                    
                }
            }
        }.padding(.vertical, 10).padding(.trailing, 8)
    }
    
    func submitAction() {
        guard let url = URL(string: "http://127.0.0.1:8000") else {
            print("Invalid URL")
            return
        }

        let task = URLSession.shared.dataTask(with: url) { data, response, error in
            if let error = error {
                print("Error: \(error)")
            } else if let data = data {
                if let responseString = String(data: data, encoding: .utf8) {
                    print("\(responseString)")
                }
            }
        }

        task.resume()
    }
    
    func activateMicrophone() {
        print("Microphone Activated!")
    }
    
}

#Preview {
    Menu()
}
