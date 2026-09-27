import { CameraStream } from "../../components/CameraStream";
import { CameraChat } from "../../components/CameraChat";

import styles from "./CameraView.module.css";


export function CameraView() {
    return (
        <main className={styles.page}>
            <CameraStream />
            <CameraChat />
        </main>
    );
}


