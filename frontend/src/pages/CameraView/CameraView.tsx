import { CameraStream } from "../../components/CameraStream";
import { CameraChat } from "../../components/CameraChat";

import styles from "./CameraView.module.css";


export function CameraView() {
    return (
        <div className={styles.page}>
            <section className={styles.workspace}>
                <CameraStream />
                <CameraChat />
            </section>
        </div>
    );
}
