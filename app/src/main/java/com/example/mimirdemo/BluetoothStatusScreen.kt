package com.example.mimirdemo

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavHostController

@Composable
fun BluetoothStatusScreen(navController: NavHostController) {
    var connectionStatus by remember { mutableStateOf("Not Connected") } // Placeholder status

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(text = "Bluetooth Status", style = MaterialTheme.typography.headlineLarge)

        Spacer(modifier = Modifier.height(24.dp))

        // Display connection status
        Text(text = "Status: $connectionStatus", style = MaterialTheme.typography.bodyLarge)

        Spacer(modifier = Modifier.height(24.dp))

        // Scan for Bluetooth devices button (Functionality will be added later)
        Button(
            onClick = {
                // Placeholder: Update the status (Later this will scan for devices)
                connectionStatus = "Scanning..."
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Scan for Devices")
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Back to Main Menu button
        Button(
            onClick = { navController.navigate("mainMenu") },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Back to Main Menu")
        }
    }
}
