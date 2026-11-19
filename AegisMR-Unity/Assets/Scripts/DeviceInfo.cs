using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit;
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

    private XRGrabInteractable grab;

    // Find the grab component on this device once
    private void Awake()
    {
        grab = GetComponent<XRGrabInteractable>();
    }

    // Listen for grabs only while this device is active
    private void OnEnable()
    {
        grab.selectEntered.AddListener(OnGrabbed);
        grab.selectExited.AddListener(OnReleased);
    }

    // Stop listening when the device is disabled or destroyed
    private void OnDisable()
    {
        grab.selectEntered.RemoveListener(OnGrabbed);
        grab.selectExited.RemoveListener(OnReleased);
    }

    // Called by XRI when a hand or controller grabs the device
    private void OnGrabbed(SelectEnterEventArgs args)
    {
        Debug.Log($"Grabbed {deviceName}");
    }

    // Called by XRI when the device is let go
    private void OnReleased(SelectExitEventArgs args)
    {
        Debug.Log($"Released {deviceName}");
    }
}
