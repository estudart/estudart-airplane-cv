

interface Props {
    cluster: string
}

export default function DetectionGalleryCard({ cluster }: Props) {

    return (
        <main>
            <div>{cluster}</div>
        </main>
    )
}