package com.example.mimirdemo

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import com.example.mimirdemo.ui.theme.MimirDemoTheme

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CameraScreen(navController: NavHostController) {
    CameraPermissionRequest {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Black)
        ) {
            // Display the Camera Preview
            CameraPreview()

            // Top bars with Mimir and Object Mode text
            Column {
                // First Top Bar for Mimir
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(60.dp)
                        .background(Color(0xFF9b9ca5)),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "Mimir",
                        fontSize = 40.sp,
                        fontFamily = FontFamily(Font(R.font.pac)),
                        color = Color.White,
                        style = TextStyle(lineHeight = 40.sp)
                    )
                }

                // Second Top Bar for Object Mode
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(50.dp)
                        .background(Color(0x801C1C1E)),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "OBJECT MODE",
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color.White
                    )
                }
            }

            // Bottom Button with speaker icon
            Box(
                modifier = Modifier
                    .fillMaxSize(),
                contentAlignment = Alignment.BottomCenter
            ) {
                Button(
                    onClick = { navController.navigate("mainMenu") },
                    shape = CircleShape,
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF404040)),
                    modifier = Modifier
                        .size(100.dp)
                        .padding(bottom = 32.dp)
                ) {
                    Icon(
                        painter = painterResource(id = R.drawable.sound),
                        contentDescription = "Speaker Icon",
                        modifier = Modifier.size(50.dp),
                        tint = Color.White
                    )
                }
            }
        }
    }
}
