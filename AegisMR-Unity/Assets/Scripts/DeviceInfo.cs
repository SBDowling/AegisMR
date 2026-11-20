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

    // A quick pinch that barely moves the device counts as a tap
    [SerializeField] private float maxTapSeconds = 0.4f;
    [SerializeField] private float maxTapDistance = 0.02f;
    private float grabStartTime;
    private Vector3 grabStartPosition;

    // The info panel shown above this device when it is tapped
    [SerializeField] private DevicePopup popupPrefab;
    [SerializeField] private float popupHeight = 0.3f;
    private DevicePopup popup;

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

    // Called by XR Interactable when a hand or controller grabs the device
    private void OnGrabbed(SelectEnterEventArgs args)
    {
        Debug.Log($"Grabbed {deviceName}");
        // Remember when and where the grab started
        grabStartTime = Time.time;
        grabStartPosition = transform.position;
    }

    // Called by XR Interactable when the device is let go
    private void OnReleased(SelectExitEventArgs args)
    {
        Debug.Log($"Released {deviceName}");
        // Short and still means a tap, otherwise it was a normal grab
        float heldFor = Time.time - grabStartTime;
        float movedBy = Vector3.Distance(grabStartPosition, transform.position);
        if (heldFor <= maxTapSeconds && movedBy <= maxTapDistance)
        {
            Debug.Log($"Tapped {deviceName}");
            TogglePopup();
        }
    }

    // Each tap shows the popup, the next tap hides it again
    private void TogglePopup()
    {
        // Make the popup the first time this device is tapped
        if (popup == null)
        {
            popup = Instantiate(popupPrefab);
            popup.SetDetails(deviceName, deviceType, ipAddress, macAddress);
            popup.gameObject.SetActive(false);
        }

        bool show = !popup.gameObject.activeSelf;
        popup.gameObject.SetActive(show);

        // Put it above the device, turned to face the learner
        if (show)
        {
            popup.transform.position = transform.position + Vector3.up * popupHeight;
            popup.transform.rotation = Quaternion.LookRotation(popup.transform.position - Camera.main.transform.position);
        }
    }
}
