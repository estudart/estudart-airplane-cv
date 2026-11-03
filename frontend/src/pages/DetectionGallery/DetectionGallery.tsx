import DetectionGalleryCard from "../../components/DetectionGalleryCard"

export default function DetectionSearch() {
    const detectionClusters = ['airplane', 'helicopter', 'bird'];
    return (
        <main>
            {detectionClusters.map(cluster => 
                <DetectionGalleryCard cluster={cluster}/>
            )}
        </main>
    )
}
