package com.example.mimirdemo
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import android.Manifest
import android.content.pm.PackageManager
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.ui.platform.LocalContext
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat


class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MyAppWithPermissions()
        }
    }
}

@Composable
fun MyAppWithPermissions() {
    val context = LocalContext.current

    val permissions = arrayOf(
        Manifest.permission.BLUETOOTH_SCAN,
        Manifest.permission.BLUETOOTH_CONNECT,
        Manifest.permission.ACCESS_FINE_LOCATION,
        Manifest.permission.ACCESS_COARSE_LOCATION
    )

    // Check if all permissions are granted
    val allPermissionsGranted = remember {
        permissions.all { permission ->
            ContextCompat.checkSelfPermission(context, permission) == PackageManager.PERMISSION_GRANTED
        }
    }

    // Create a launcher for requesting multiple permissions
    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestMultiplePermissions()
    ) { permissionsResult ->
        val granted = permissionsResult.values.all { it }
        if (!granted) {
            // Show a toast if permissions are not granted
            Toast.makeText(context, "Bluetooth permissions are required.", Toast.LENGTH_SHORT).show()
        }
    }

    // Request permissions if not all are granted
    LaunchedEffect(allPermissionsGranted) {
        if (!allPermissionsGranted) {
            permissionLauncher.launch(permissions)
        }
    }

    // Show the main content if all permissions are granted
    if (allPermissionsGranted) {
        MyApp()
    }
}



@Composable
fun MyApp() {
    val navController = rememberNavController()

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        content = { innerPadding ->
            NavHost(
                navController = navController,
                startDestination = "mainMenu",
                modifier = Modifier.padding(innerPadding)
            ) {
                composable("mainMenu") { MainMenuScreen(navController) }
                composable("bluetoothStatus") { BluetoothStatusScreen(navController) }
                composable("recipeScreen") { RecipeScreen(navController) }
                composable("modeScreen") { ModeScreen(navController) }
                composable("cameraScreen") { CameraScreen(navController) }
            }
        }
    )
}