using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit.Interactables;

// Holds a device's details and notices when the learner taps it
[RequireComponent(typeof(XRGrabInteractable))]
public class DeviceInfo : MonoBehaviour
{
    // Placeholder details until the backend sends real ones
    [SerializeField] private string deviceName = "PC1";
    [SerializeField] private string deviceType = "pc";
    [SerializeField] private string ipAddress = "192.168.1.10";
    [SerializeField] private string macAddress = "02:00:00:00:00:01";
}
