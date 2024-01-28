import SwiftUI
import Speech

struct Menu: View {
    @State private var userInput: String = ""
    @State private var isRecording: Bool = false

    var body: some View {
        Form {
            Section {
                CustomTextFieldWithButton(
                    userInput: $userInput,
                    isRecording: $isRecording,
                    submitAction: {
                        handleSubmit()
                    },
                    activateMicrophone: {
                    if isRecording {
                        print("Recording stopped")
                    } else {
                        print("Recording started")
                    }
                    isRecording.toggle()
                })
                .padding(.vertical, 10)
                .background(Color.clear)
            }
        }.font(.system(size: 20))
        .frame(width: 400, height: 50)
    }
    
    func handleSubmit() {
        guard let url = URL(string: "http://127.0.0.1:8000/query") else {
            print("Invalid URL")
            return
        }

        guard let jsonData = try? JSONSerialization.data(withJSONObject: ["question": userInput]) else {
            print("Error encoding JSON data")
            return
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = jsonData

        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                print("Error: (error)")
            } else if let data = data {
                if let responseString = String(data: data, encoding: .utf8) {
                    print("(responseString)")
                }
            }
        }

        task.resume()
    }
    
}

struct CustomTextFieldWithButton: View {
    @Binding var userInput: String
    @Binding var isRecording: Bool
    var submitAction: () -> Void
    var activateMicrophone: () -> Void

    var body: some View {
        TextField("", text: $userInput, prompt: Text("Ask anything"))
            .frame(height: 35)
            .textFieldStyle(PlainTextFieldStyle())
            .padding([.horizontal], 4)
            .cornerRadius(200)
            .overlay(RoundedRectangle(cornerRadius: 6).stroke(Color.clear))
            .padding([.leading], 8)
            .overlay(
                HStack {
                    Spacer()
                    Button(action: {
                        if userInput.isEmpty {
                            activateMicrophone()
                        } else {
                            submitAction()
                        }
                    }) {
                        Image(systemName: isRecording ? "stop.circle.fill" : (userInput.isEmpty ? "mic.fill" : "paperplane.fill"))
                            .font(.system(size: 16))
                            .padding(.trailing, 8)
                    }.buttonStyle(PlainButtonStyle())
                }
            )
        .padding(.trailing, 10)
    }
    
}

#Preview {
    Menu()
}
