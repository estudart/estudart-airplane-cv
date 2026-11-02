import { Routes, Route, Navigate } from 'react-router-dom';

import "./index.css";
import Layout from "./components/Layout";
import { CameraView } from "./pages/CameraView/CameraView";


export default function App() {
    return (
        <Routes>
            <Route path="/" element={<Navigate to="/camera-view" replace />} />
            <Route element={<Layout />}>
                <Route path="/camera-view" element={<CameraView />} />
            </Route>
        </Routes>
    )

};
