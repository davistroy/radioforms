fn main() {
    // OPTIMIZATION: Enable SQLx offline mode for faster compilation
    println!("cargo:rustc-env=SQLX_OFFLINE=true");
    
    tauri_build::build()
}
