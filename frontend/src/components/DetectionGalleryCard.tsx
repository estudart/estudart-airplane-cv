

export default function DetectionGalleryCard() {
    const detectionClusters = ['airplane', 'helicopter', 'bird'];
    return (
        <main>
            {detectionClusters.map(cluster => 
                <div>{cluster}</div>
            )}
        </main>
    )
}