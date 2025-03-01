import os
from autogen import GroupChat, GroupChatManager
from services.agents import (
    product_manager,
    engineer,
    designer,
    database_analyst,
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
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEYが設定されていません。.envファイルを確認してください。"
            )
        self.display_names = {
            "ProductManager": "プロダクトマネージャー",
            "Engineer": "エンジニア",
            "Designer": "デザイナー",
            "DatabaseAnalyst": "データアナリスト",
        }

    def create_group_chat(self, max_rounds=10):
        """
        グループチャットを作成する
        """
        select_speaker_llm_config = {
            "config_list": [
                {
                    "model": "gpt-4o-mini",
                    "api_key": self.openai_api_key,
                }
            ]
        }

        group_chat = GroupChat(
            agents=self.participants,
            messages=[],
            max_round=max_rounds,
            speaker_selection_method="auto",
            allow_repeat_speaker=False,
            select_speaker_message_template=(
                "以下の会話を読み、次に発言すべき専門家を選んでください"
                "リストから一つだけ、エージェント名のみを返してください"
            ),
            send_introductions=True,
        )

        return GroupChatManager(
            groupchat=group_chat,
            llm_config=select_speaker_llm_config,
        )

    def start_software_design_discussion(self, user_message, max_turns=10):
        """
        ユーザーの要件に基づいて設計議論を開始する
        """
        manager = self.create_group_chat(max_rounds=max_turns)

        initial_message = f"""
クライアントから次のような要件が提示されました：「{user_message}」
この要件について、それぞれの専門的観点から議論し、最適な設計と実装方法を考えましょう。
対話の中で質問を投げかけ、他の専門家の視点を引き出すことも重要です。

最初に、プロダクトマネージャーが初期評価と他の専門家への質問から始めてください。
"""
        manager.initiate_chat(
            product_manager,
            message=initial_message,
        )

        conversation_history = self._format_conversation(manager.groupchat.messages)

        return conversation_history

    def _format_conversation(self, messages):
        """会話履歴を読みやすい形式に整形する"""
        formatted_text = ""
        for msg in messages:
            sender = msg.get("sender", "Unknown")
            # 表示名に変換（マッピングにない場合はそのまま使用）
            display_name = self.display_names.get(sender, sender)
            content = msg.get("content", "")
            formatted_text += f"\n\n## {display_name}:\n\n{content}\n"
            formatted_text += "\n---\n"

        return formatted_text


# シングルトンインスタンスを作成
software_design_group = SoftwareDesignGroupChat()
