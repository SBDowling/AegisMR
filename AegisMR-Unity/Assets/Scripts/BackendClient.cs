using System;
using System.Net.WebSockets;
using System.Threading;
using UnityEngine;

public class BackendClient : MonoBehaviour
{
    // Connects to the Python backend when Play mode starts

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
        }

    }

}
