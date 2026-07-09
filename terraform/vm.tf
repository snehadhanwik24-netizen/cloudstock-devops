resource "azurerm_network_interface" "cloudstock_nic" {
  name                = "cloudstock-nic"
  location            = var.location
  resource_group_name = azurerm_resource_group.cloudstock_rg.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.cloudstock_subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.cloudstock_public_ip.id
  }
}

resource "azurerm_linux_virtual_machine" "cloudstock_vm" {
  name                = "cloudstock-vm"
  resource_group_name = azurerm_resource_group.cloudstock_rg.name
  location            = var.location
  size = "Standard_B2s"
  admin_username = "azureuser"

  network_interface_ids = [
    azurerm_network_interface.cloudstock_nic.id
  ]

  admin_password                  = "CloudStock@12345"
  disable_password_authentication = false

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "ubuntu-24_04-lts"
    sku       = "server"
    version   = "latest"
  }
}