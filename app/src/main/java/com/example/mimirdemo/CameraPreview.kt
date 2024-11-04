package com.example.mimirdemo

import android.annotation.SuppressLint
import android.util.Log
import android.view.ViewGroup
import android.widget.FrameLayout
import androidx.camera.core.CameraSelector
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import androidx.lifecycle.LifecycleOwner
import com.google.common.util.concurrent.ListenableFuture

@SuppressLint("UnsafeOptInUsageError")
@Composable
fun CameraPreview() {
    val context = LocalContext.current
    val lifecycleOwner = LocalContext.current as LifecycleOwner
    var previewView: PreviewView? by remember { mutableStateOf(null) }

    // Initialize CameraProvider
    val cameraProviderFuture: ListenableFuture<ProcessCameraProvider> =
        ProcessCameraProvider.getInstance(context)

    AndroidView(
        factory = { ctx ->
            // Create PreviewView as the container for the camera feed
            PreviewView(ctx).also { previewView = it }
        },
        modifier = Modifier.fillMaxSize(),
        update = { view ->
            val cameraProvider: ProcessCameraProvider = cameraProviderFuture.get()
            val preview = Preview.Builder().build()

            // Select the back camera as the default
            val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA

            // Connect the preview to the camera lifecycle
            preview.setSurfaceProvider(previewView?.surfaceProvider)

            try {
                // Unbind use cases before rebinding
                cameraProvider.unbindAll()

                // Bind the camera to the lifecycle and preview
                cameraProvider.bindToLifecycle(
                    lifecycleOwner, cameraSelector, preview
                )
            } catch (e: Exception) {
                Log.e("CameraPreview", "Use case binding failed", e)
            }
        }
    )
}
