using TMPro;
using UnityEngine;

// The floating info panel that shows a device's details
public class DevicePopup : MonoBehaviour
{
    // The two text boxes inside the popup prefab, dragged in through the Inspector
    [SerializeField] private TMP_Text titleText;
    [SerializeField] private TMP_Text detailsText;

    // Writes a device's details into the popup
    public void SetDetails(string deviceName, string deviceType, string ipAddress, string macAddress)
    {
        titleText.text = deviceName;
        detailsText.text = $"Type: {deviceType}\nIP: {ipAddress}\nMAC: {macAddress}";
    }
}
