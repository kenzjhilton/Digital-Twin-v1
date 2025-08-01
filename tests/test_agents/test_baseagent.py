from base_agent import BaseSupplyChainAgent

class TestAgent(BaseSupplyChainAgent):
    def process_material(self, material, quantity):
        return f"Processed {quantity} kg of {material}"

# Test it
if __name__ == "__main__":
    agent = TestAgent("MINE_001", "Test Mining Agent", 1000.0)
    print("Success! Agent created.")
    print(agent.get_status())