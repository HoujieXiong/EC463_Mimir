package com.example.mimirdemo

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import com.example.mimirdemo.R

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ModeScreen(navController: NavHostController) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF9b9ca5)) // Gray background (adjust color if needed)
    ){
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(60.dp) // Adjust height as necessary
                .background(Color(0xFF9b9ca5)),
            contentAlignment = Alignment.Center
        ) {
            // Replace this with an Image if you have a logo
            Text(
                text = "Mimir", // Mimir Logo Text
                fontSize = 40.sp,
                fontFamily = FontFamily(Font(R.font.pac)),
                //fontWeight = FontWeight.Bold,
                color = Color.White,
                style = TextStyle(
                    lineHeight = 40.sp // Match the font size to reduce the extra spacing
                )
            )
        }
        TopAppBar(
            title = {
                Box(
                    modifier = Modifier.fillMaxWidth(), // Make the Box take up full width
                    contentAlignment = Alignment.Center // Center-align the text
                ) {
                    Text(
                        text = "CHOOSE A MODE",
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color.Black
                    )
                }
            },
            colors = TopAppBarDefaults.topAppBarColors(
                containerColor = Color(0xFFFFFFFF) // Dark background for top bar
            )
        )

        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(10.dp) // Adjust the height as needed
                .background(Color(0xFF000000)) // Set the color of the space
        )



        Column(
            modifier = Modifier
                .fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.SpaceEvenly
        ) {
            // Environment Mode button
            Button(
                onClick = { navController.navigate("cameraScreen") }, // Navigate to Environment
                shape = RoundedCornerShape(0.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(350.dp), // Adjust height as needed
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF8C8C8C)) // Background color of the button
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    Image(
                        painter = painterResource(id = R.drawable.environment), // Your environment icon
                        contentDescription = "Environment Icon",
                        modifier = Modifier.size(200.dp),
                        contentScale = ContentScale.Fit
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "Environment",
                        fontSize = 30.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color.White
                    )
                }
            }

            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(10.dp) // Adjust the height as needed
                    .background(Color(0xFF000000)) // Set the color of the space
            )
            // Object Mode button
            Button(
                onClick = { navController.navigate("cameraScreen") }, // Navigate to Object mode
                shape = RoundedCornerShape(0.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(350.dp), // Adjust height as needed
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF8C8C8C)) // Background color of the button
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    Image(
                        painter = painterResource(id = R.drawable.`object`), // Your object icon
                        contentDescription = "Object Icon",
                        modifier = Modifier.size(200.dp),
                        contentScale = ContentScale.Fit
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "Object",
                        fontSize = 30.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color.White
                    )
                }
            }
        }
    }
}
