window.addEventListener("load", function () {
    const mindmapUrl = window.mindmapUrl;

    // ✅ Use directly from UMD (ReactFlow is defined globally by the UMD script)
    if (!window.ReactFlow) {
        console.error("❌ ReactFlow not loaded properly.");
        return;
    }

    console.log("✅ ReactFlow loaded:", window.ReactFlow);

    const { ReactFlow, Controls, Background, MiniMap } = window.ReactFlow;

    const generateMindMapBtn = document.getElementById("generate-mindmap");
    const mindmapContainer = document.getElementById("reactflow-container");
    const mindmapLoading = document.getElementById("mindmap-loading");
    const mindmapError = document.getElementById("mindmap-error");
    const errorMessage = document.getElementById("error-message");

    let mindMapData = null;
    let reactFlowInstance = null;

    const tabTrigger = document.getElementById("mindmap-tab");
    if (tabTrigger) {
        tabTrigger.addEventListener("shown.bs.tab", function () {
            if (mindMapData && !reactFlowInstance) {
                initializeReactFlow(mindMapData);
            }
        });
    }

    if (generateMindMapBtn) {
        generateMindMapBtn.addEventListener("click", function () {
            console.log("🧠 Generate Mind Map clicked");
            generateMindMap();
        });
    }

    function generateMindMap() {
        mindmapLoading.classList.remove("d-none");
        mindmapContainer.classList.add("d-none");
        mindmapError.classList.add("d-none");

        fetch(mindmapUrl, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Content-Type": "application/json"
            }
        })
        .then(response => {
            if (!response.ok) throw new Error("Server error: " + response.statusText);
            return response.json();
        })
        .then(data => {
            if (data.error) throw new Error(data.error);

            mindMapData = data.mindmap;

            mindmapLoading.classList.add("d-none");
            mindmapContainer.classList.remove("d-none");

            initializeReactFlow(mindMapData);
        })
        .catch(error => {
            mindmapLoading.classList.add("d-none");
            mindmapError.classList.remove("d-none");
            errorMessage.textContent = error.message || "Failed to generate mind map.";
            console.error("Mind map error:", error);
        });
    }

    function initializeReactFlow(data) {
        let flowData;
        try {
            flowData = typeof data === 'string' ? JSON.parse(data) : data;
        } catch (e) {
            console.error("❌ Failed to parse mind map data:", e);
            mindmapError.classList.remove("d-none");
            errorMessage.textContent = "Failed to parse mind map data.";
            return;
        }

        const styledNodes = flowData.nodes.map(node => ({
            ...node,
            style: {
                background: 'linear-gradient(45deg, #4e73df, #36b9cc)',
                color: 'white',
                padding: '10px',
                borderRadius: '8px',
                boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
                fontSize: '12px',
                textAlign: 'center',
                width: 'auto',
                maxWidth: '150px'
            }
        }));

        const styledEdges = flowData.edges.map(edge => ({
            ...edge,
            style: {
                stroke: '#4e73df',
                strokeWidth: 2
            },
            animated: true,
            type: 'smoothstep'
        }));

        const FlowWithProvider = () => {
            const [nodes, setNodes] = React.useState(styledNodes);
            const [edges, setEdges] = React.useState(styledEdges);

            return React.createElement(
                "div",
                { style: { width: "100%", height: "100%" } },
                React.createElement(ReactFlow, {
                    nodes,
                    edges,
                    onInit: (instance) => {
                        reactFlowInstance = instance;
                        instance.fitView();
                        console.log("🌿 Flow initialized");
                    },
                    fitView: true
                }, [
                    React.createElement(Controls, { position: "bottom-right" }),
                    React.createElement(Background, { color: "#aaa", gap: 16 }),
                    React.createElement(MiniMap, {})
                ])
            );
        };

        ReactDOM.render(
            React.createElement(FlowWithProvider),
            mindmapContainer
        );
    }

    function getCookie(name) {
        const cookieValue = document.cookie
            .split("; ")
            .find(row => row.startsWith(name + "="));
        return cookieValue ? decodeURIComponent(cookieValue.split("=")[1]) : null;
    }
});