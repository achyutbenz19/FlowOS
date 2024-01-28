import SwiftUI

struct Workflows: View {
    @State private var workflowNames: [String] = []

    var body: some View {
        VStack {
            HStack {
                Text("Workflows").bold()
                Spacer()
            }.padding(.leading, 8)

            Divider()

            VStack {
                ForEach(workflowNames, id: \.self) { name in
                    SingleWorkflow(workflowName: name)
                }
            }
        }
        .onAppear(perform: fetchWorkflows)
        .frame(width: 150)
        .padding(.vertical, 10)
        .padding(.horizontal, 5)
    }

    func fetchWorkflows() {
        guard let url = URL(string: "http://127.0.0.1:8000/workflows") else {
            print("Invalid URL")
            return
        }

        URLSession.shared.dataTask(with: url) { data, response, error in
            if let error = error {
                print("Error: \(error.localizedDescription)")
                return
            }

            guard let httpResponse = response as? HTTPURLResponse, (200...299).contains(httpResponse.statusCode) else {
                print("Invalid response")
                return
            }

            if let data = data {
                do {
                    let decoder = JSONDecoder()
                    let workflowNames = try decoder.decode([String].self, from: data)
                    print("Received workflow names: \(workflowNames)")
                    DispatchQueue.main.async {
                        self.workflowNames = workflowNames
                    }
                } catch {
                    print("Error decoding JSON: \(error.localizedDescription)")
                }
            }
        }.resume()
    }
}


struct SingleWorkflow: View {
    var workflowName: String
    @State private var isHovered = false
    
    var body: some View {
        HStack {
            Image(systemName: "cube.transparent")
                .font(Font.system(size: 14))
            Text(workflowName)
            Spacer()
        }
        .onTapGesture {
            handleTap()
        }
        .padding(.vertical, 4)
        .padding(.horizontal, 8)
        .background(RoundedRectangle(cornerRadius: 6)
                        .fill(isHovered ? Color.gray : Color.clear))
        .onHover { hovering in
            withAnimation {
                self.isHovered = hovering
            }
        }
    }
    
    func handleTap() {
        guard let url = URL(string: "http://127.0.0.1:8000/query") else {
            print("Invalid URL")
            return
        }

        var requestBody: [String: Any] = ["question": "run workflow " + workflowName]

        requestBody["is_voice"] = true

        guard let jsonData = try? JSONSerialization.data(withJSONObject: requestBody) else {
            print("Error encoding JSON data")
            return
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = jsonData

        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                if let error = error {
                    print("Error: \(error)")
                } else if let data = data {
                    if let responseString = String(data: data, encoding: .utf8),
                       let jsonData = responseString.data(using: .utf8),
                       let jsonResponse = try? JSONSerialization.jsonObject(with: jsonData) as? [String: Any],
                       let responseDict = jsonResponse["response"] as? [String: Any],
                       let response = responseDict["output"] as? String {
                           var responseText = response
                    }
                }
            }
        }
        task.resume()
    }

    
}


#Preview {
    Workflows()
}
