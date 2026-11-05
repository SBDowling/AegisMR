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

}
