import { Routes, Route } from 'react-router-dom';

import "./index.css";
import Layout from "./components/Layout";
import { CameraView } from "./pages/CameraView/CameraView";


export default function App() {
    return (
        <div>
            <Routes>
                <Route element={<Layout />}>
                <Route path="/camera-view" element={<CameraView />} />
                </Route>
            </Routes>
        </div>
    )

};
