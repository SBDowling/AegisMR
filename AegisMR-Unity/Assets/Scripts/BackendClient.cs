using System;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;

// Connects to the Python backend when Play mode starts
public class BackendClient : MonoBehaviour
{
    // Shown in the Inspector so the address can change without editing code
    [SerializeField] private string serverURL = "ws://localhost:8765";

    private ClientWebSocket socket;

    private async void Start()
    {
        socket = new ClientWebSocket();
        try
        {
            await socket.ConnectAsync(new Uri(serverURL), CancellationToken.None);
            Debug.Log($"Connected to the backend server at {serverURL}");
        }
        catch (Exception e)
        {
            Debug.LogWarning($"Could not connect: {e.Message}. Is the Python server running?");
            return;
        }

        // Start listening once connected
        await ReceiveLoop();
    }

    // Waits for one message from the server and logs it as text
    private async Task ReceiveLoop()
    {
        var buffer = new byte[8192];
        try
        {
            var result = await socket.ReceiveAsync(new ArraySegment<byte>(buffer), CancellationToken.None);
            string text = Encoding.UTF8.GetString(buffer, 0, result.Count);
            Debug.Log($"Received: {text}");
        }
        catch (Exception e)
        {
            Debug.LogWarning($"Connection lost: {e.Message}");
        }
    }

    private void OnDestroy()
    {
        // Close the connection when Play mode stops
        socket?.Dispose();
    }
}
