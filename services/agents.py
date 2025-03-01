import os
from dotenv import load_dotenv
from autogen import ConversableAgent, GroupChat, GroupChatManager


load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError(
        "OPENAI_API_KEYが設定されていません。.envファイルを確認してください。"
    )

llm_config = {
    "config_list": [
        {
            "model": "gpt-4o-mini",
            "api_key": openai_api_key,
        },
    ],
    "temperature": 0.7,
    "timeout": 120,
}

product_manager = ConversableAgent(
    name="ProductManager",
    system_message="""あなたはPdMエージェントです。ユーザーからのタスク依頼を最初に受け取ります。ユーザー柄のタスク依頼を最初に受け取ります

自分自身ではエンジニアやデザインに関する選定をしないで他のエージェントに依頼するようにしてください。
必要に応じてバックエンドエンジニア、フロントエンドエンジニア、デザイナーの各エージェントにタスクを依頼してください。
最後にタスクを終了する責任を持っています。依頼の最終回答が得られてかつアウトプットのクオリティがプロとして十分と判断した場合、最終的な結果を出力してください。
""",
    llm_config=llm_config,
    human_input_mode="NEVER",
)

engineer = ConversableAgent(
    name="Engineer",
    system_message="""あなたは実装を担当するソフトウェアエンジニアです。
エンジニアのテックリードとして技術選定と設計と実装をしてください。
UI/UXやデザインはデザイナーに相談し、仕様や企画はPdMに相談してください。
データ構造や命名はデータアナリストと相談してください。""",
    llm_config=llm_config,
    human_input_mode="NEVER",
)

designer = ConversableAgent(
    name="Designer",
    system_message="""あなたはUIUXデザイナーです。シニアデザイナーとしてデザインおよび、
    UIやUXのガイドラインを策定してください。デザインの実装についてはエンジニアと相談してください。""",
    llm_config=llm_config,
    human_input_mode="NEVER",
)

database_analyst = ConversableAgent(
    name="DatabaseAnalyst",
    system_message="""あなたはデータアナリストです。
データアナリストのエキスパートとして、データ戦略の立案、設計、分析、解析をしてください。
データ設計や具体的な実装についてはエンジニアに相談してください。""",
    llm_config=llm_config,
    human_input_mode="NEVER",
)


class SoftwareDesignGroupChat:
    """
    ソフトウェア設計のためのグループチャットを管理するクラス
    """

    def __init__(self):
        self.participants = [
            product_manager,
            engineer,
            designer,
            database_analyst,
        ]

    def create_group_chat(self, max_rounds=10):
        """
        グループチャットを作成する
        """
        group_chat = GroupChat(
            agents=self.participants,
            messages=[],
            max_round=max_rounds,
            speaker_selection_method="auto",
        )
        return GroupChatManager(groupchat=group_chat)

    def start_software_design_discussion(self, user_message, max_turns=10):
        """
        ユーザーの要件に基づいて設計議論を開始する
        """
        manager = self.create_group_chat(max_rounds=max_turns)

        initial_message = f"""
クライアントから次のような要件が提示されました：「{user_message}」
この要件について、それぞれの専門的観点から議論し、最適な設計と実装方法を考えましょう。
各専門家は必ず自分の専門分野からの視点を共有してください。
"""

        manager.initiate_chat(
            product_manager,
            message=initial_message,
        )

        conversation_history = self._format_conversation(manager.groupchat.messages)

        return conversation_history

    def _format_conversation(self, messages):
        """会話履歴を読みやすい形式に整形する"""
        display_names = {
            "ProductManager": "プロダクトマネージャー",
            "Engineer": "エンジニア",
            "Designer": "デザイナー",
            "DatabaseAnalyst": "データアナリスト",
        }

        formatted_text = ""
        for msg in messages:
            sender = msg.get("sender", "Unknown")
            display_name = display_names.get(sender, sender)
            content = msg.get("content", "")
            formatted_text += f"\n\n## {display_name}:\n\n{content}\n"
            formatted_text += "\n---\n"

        return formatted_text


software_design_group = SoftwareDesignGroupChat()
